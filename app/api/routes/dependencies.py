from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.exceptions import AuthenticationError, NotFoundError
from app.repositories import customer_repository
from app.schemas.customerschema import Customer
from app.tokens import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)






def get_current_customer(
    customer_id: int,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Customer:
    """Own-account rule for routes with a {customer_id} in the path.
    401 if there is no valid token (or the customer is deactivated),
    403 if the token belongs to someone else, 404 if the account does not exist."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not signed in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        signed_in_id = verify_access_token(credentials.credentials)
    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if signed_in_id != customer_id:
        raise HTTPException(
            status_code=403, detail="You do not have access to this account"
        )

    customer = customer_repository.get_customer_by_id(signed_in_id)
    if customer is None:
        raise NotFoundError("Customer not found")
    if not customer.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return customer


def get_signed_in_customer(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Customer:
    """For routes without a {customer_id} in the path (restaurants).
    401 if there is no valid token or the customer is deactivated."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not signed in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        signed_in_id = verify_access_token(credentials.credentials)
    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    customer = customer_repository.get_customer_by_id(signed_in_id)
    if customer is None or not customer.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return customer