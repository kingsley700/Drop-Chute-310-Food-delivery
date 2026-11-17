from fastapi import APIRouter, HTTPException

from app.exceptions import ConflictError
from app.schemas.customerschema import CustomerCreate, CustomerResponse
from app.services import customer_services

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=201,
    summary="Register a new customer",
    responses={
        201: {"description": "Customer registered. The password is never returned."},
        409: {"description": "A customer with this email already exists."},
        422: {
            "description": "Missing or invalid input (name, email, password or delivery address)."
        },
    },
)
def register_customer(data: CustomerCreate):
    """Creates a customer account from the registration request"""
    try:
        return customer_services.register_customer(data)
    except ConflictError as error:
        raise HTTPException(status_code=409, detail=str(error))
