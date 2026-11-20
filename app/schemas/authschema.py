from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request body for sign-in (POST /auth/login)."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """What sign-in returns on success."""

    access_token: str
    token_type: str = "bearer"