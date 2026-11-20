
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.cart import CartItem


# Order creation request
class OrderCreate(BaseModel):
    customer_id: int


# Order model
class Order(BaseModel):
    id: int
    customer_id: int
    restaurant_id: UUID
    items: list[CartItem]
    subtotal: float
    tax: float
    total: float
    transaction_id: str
    created_at: datetime = Field(default_factory=datetime.now)


# Order response
class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: UUID
    items: list[CartItem]
    subtotal: float
    tax: float
    total: float
    transaction_id: str
    created_at: datetime
