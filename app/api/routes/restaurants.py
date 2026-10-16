from fastapi import APIRouter
from app.services.restaurant_services import get_restaurants
from app.schemas.restaurantschemas import Restaurant

router = APIRouter()


@router.get("/restaurants", response_model=list[Restaurant],
            summary = "List all restaurants",
            description = "Returns every restaurant with its cuisine and menu items. No parameters, returns empty list if no restaurants available.",
            responses = {500: {"description": "The restaurant data file could not be read"}}
            )

def restaurant_list():
    return get_restaurants()