from pydantic import BaseModel, Field

class RestaurantItem(BaseModel):
    name: str
    price: float
    description: str | None = None

class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str
    items: list[RestaurantItem]


class RestaurantCreate(BaseModel):
    name: str
    cuisine: str
    items: list[RestaurantItem] = Field(default_factory=list)


#schema for updating a restaurant
class RestaurantUpdate(BaseModel):
    name: str | None = None
    cuisine: str | None = None


#schema for updating a menu item
class RestaurantItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None