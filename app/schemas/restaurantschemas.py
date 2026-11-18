from pydantic import BaseModel, Field

class RestaurantItem(BaseModel):
    name: str
    price: float = Field(ge=0)
    description: str | None = None
    available: bool = True

class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str
    items: list[RestaurantItem]

#schema for updating a restaurant
class RestaurantUpdate(BaseModel):
    name: str | None = None
    cuisine: str | None = None


#schema for updating a menu item
class RestaurantItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, ge=0)
    description: str | None = None