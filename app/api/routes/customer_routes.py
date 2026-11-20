from fastapi import APIRouter, Depends, HTTPException, Response

from app.exceptions import ConflictError
from app.api.routes.dependencies import get_current_customer
from app.schemas.customerschema import (
    Customer,
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
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


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="View my account",
    responses={
        200: {"description": "The customer's account details. No password or hash."},
        401: {"description": "Not signed in, or the sign-in has expired."},
        403: {"description": "The account belongs to another customer."},
        404: {"description": "The account does not exist."},
    },
)
def get_customer(customer_id: int, customer: Customer = Depends(get_current_customer)):
    """Returns the signed-in customer's own account details."""
    return customer_services.get_customer(customer_id)


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update my delivery address",
    responses={
        200: {"description": "The updated account details."},
        401: {"description": "Not signed in, or the sign-in has expired."},
        403: {"description": "The account belongs to another customer."},
        404: {"description": "The account does not exist."},
        422: {"description": "The delivery address is blank or too long."},
    },
)
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    customer: Customer = Depends(get_current_customer),
):
    """Changes the signed-in customer's delivery address."""
    return customer_services.update_customer(customer_id, data)


@router.post(
    "/{customer_id}/deactivate",
    status_code=204,
    summary="Deactivate my account",
    responses={
        204: {
            "description": "Account deactivated. The account and its history are kept."
        },
        401: {"description": "Not signed in, or the sign-in has expired."},
        403: {"description": "The account belongs to another customer."},
        404: {"description": "The account does not exist."},
    },
)
def deactivate_customer(
    customer_id: int, customer: Customer = Depends(get_current_customer)
):
    """Deactivates the signed-in customer's own account. The account is kept, not deleted."""
    customer_services.deactivate_customer(customer_id)
    return Response(status_code=204)
