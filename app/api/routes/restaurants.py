from fastapi import APIRouter
from app.services.restaurant_services import get_restaurants
from app.schemas.restaurantschemas import Restaurant

router = APIRouter()


@router.get("/restaurants", response_model=list[Restaurant])
def restaurant_list():
    return get_restaurants()