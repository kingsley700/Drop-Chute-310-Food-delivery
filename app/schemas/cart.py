
from pydantic import BaseModel

class CartCreate(BaseModel):
    """Request body for creating a cart."""
    customer_id: int


class Cart(BaseModel):
    """Cart as stored."""
    id: int
    customer_id: int
    status: str = "active"
    items: list = []


class CartResponse(BaseModel):
    """What the API returns."""
    id: int
    customer_id: int
    status: str
    items: list
