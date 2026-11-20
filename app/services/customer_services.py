from app.exceptions import ConflictError
from app.repositories import customer_repository
from app.schemas.customerschema import CustomerCreate, CustomerResponse, CustomerUpdate
from app.security import hash_password
from exceptions import NotFoundError


def register_customer(data: CustomerCreate) -> CustomerResponse:
    """Registers a new customer. Raises ConflictError if email is taken."""
    existing = customer_repository.get_customer_by_email(data.email)
    if existing is not None:
        raise ConflictError("Email is already registered")

    hashed = hash_password(data.password)
    customer = customer_repository.create_customer(
        name=data.name,
        email=data.email,
        hashed_password=hashed,
        delivery_address=data.delivery_address,
    )
    return CustomerResponse(**customer.model_dump())

def get_customer(customer_id: int) -> CustomerResponse:
    customer = customer_repository.get_customer_by_id(customer_id)
    if customer is None:
        raise NotFoundError("Customer not found")
    return CustomerResponse(**customer.model_dump())


def update_customer(customer_id: int, data: CustomerUpdate) -> CustomerResponse:
    customer = customer_repository.update_customer_address(customer_id, data.delivery_address)
    if customer is None:
        raise NotFoundError("Customer not found")
    return CustomerResponse(**customer.model_dump())

