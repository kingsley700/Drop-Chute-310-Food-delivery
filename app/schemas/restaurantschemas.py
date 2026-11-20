from uuid import UUID

from pydantic import BaseModel, Field

class RestaurantItem(BaseModel):
    name: str
    price: float = Field(ge=0)
    description: str | None = None
    available: bool = True

class Restaurant(BaseModel):
    id: UUID
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
    price: float | None = Field(default=None, ge=0)
    description: str | None = None