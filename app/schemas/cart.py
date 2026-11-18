from pydantic import BaseModel, Field


class CartCreate(BaseModel):
    """Request body for creating a cart."""
    customer_id: int


class CartItemCreate(BaseModel):
    """Request body for adding an item to a cart."""
    restaurant_id: int
    item_name: str
    quantity: int


class CartItemUpdate(BaseModel):
    """Request body for updating an item's quantity."""
    quantity: int


class CartItem(BaseModel):
    """An item inside a cart."""
    name: str
    price: float
    quantity: int


class Cart(BaseModel):
    """Cart as stored."""
    id: int
    customer_id: int
    status: str = "active"
    restaurant_id: int | None = None
    items: list[CartItem] = Field(default_factory=list)
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0


class CartResponse(BaseModel):
    """What the API returns."""
    id: int
    customer_id: int
    status: str
    restaurant_id: int | None = None
    items: list[CartItem] = Field(default_factory=list)
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0