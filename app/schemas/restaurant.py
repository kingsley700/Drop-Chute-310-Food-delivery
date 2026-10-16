from pydantic import BaseModel

class RestaurantItem(BaseModel):
    name: str
    price: float
    description: str | None = None

class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str
    items: list[RestaurantItem]

