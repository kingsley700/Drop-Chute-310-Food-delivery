from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerCreate(BaseModel):
    """Request body for registration (POST /customers)."""

    name: str = Field(..., min_length=3, max_length=40)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    delivery_address: str = Field(..., min_length=1, max_length=200)

    @field_validator("name", "delivery_address")  # To make sure name and address aren't empty
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if value == "":
            raise ValueError("must not be blank")
        return value


class Customer(BaseModel):
    """The customer as stored. Never returned to clients directly."""

    id: int
    name: str
    email: EmailStr
    hashed_password: str
    delivery_address: str


class CustomerResponse(BaseModel):
    """What the API returns. No password and no hash."""

    id: int
    name: str
    email: EmailStr
    delivery_address: str
