from fastapi import APIRouter
from app.api.restaurant_services import get_restaurants

router = APIRouter()

@router.get("/restaurants")
def restaurant_list():
    return get_restaurants()