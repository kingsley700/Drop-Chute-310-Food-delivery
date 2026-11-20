from fastapi import APIRouter, HTTPException

from app.exceptions import AuthenticationError
from app.schemas.authschema import LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Sign in",
    responses={
        200: {"description": "Signed in. Returns an access token."},
        401: {"description": "Invalid email or password."},
        422: {"description": "Missing or malformed email or password."},
    },
)
def login(data: LoginRequest):
    """Checks the email and password and returns an access token."""
    try:
        token = auth_service.login(data)
    except AuthenticationError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=token)