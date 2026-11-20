from app.exceptions import AuthenticationError
from app.repositories import customer_repository
from app.schemas.authschema import LoginRequest
from app.security import verify_password
from app.tokens import create_access_token

# One message for both failures, so response never reveals if email exists.
INVALID_LOGIN_MESSAGE = "Invalid email or password"


def login(data: LoginRequest) -> str:
    """Returns an access token for valid credentials.
    Raises AuthenticationError for an unknown email or a wrong password."""
    customer = customer_repository.get_customer_by_email(data.email)
    if customer is None:
        raise AuthenticationError(INVALID_LOGIN_MESSAGE)
    if not verify_password(data.password, customer.hashed_password):
        raise AuthenticationError(INVALID_LOGIN_MESSAGE)
    return create_access_token(customer.id)