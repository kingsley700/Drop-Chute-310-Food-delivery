from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from app.exceptions import NotFoundError
from fastapi.responses import JSONResponse
from app.api.routes.restaurants import router as restaurant_router
from app.schemas.health import HealthResponse
from app.schemas.home import HomeResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.cart import router as cart_router
from app.api.routes import customer_routes, auth_routes
from app.api.routes.checkout_routes import router as checkout_router

app = FastAPI()
app.include_router(checkout_router)
app.include_router(auth_routes.router)
app.include_router(customer_routes.router)


@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    """422 response without FastAPI's default "input" field, echoing submitted password back to client."""
    errors = []
    for error in exc.errors():
        errors.append(
            {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        )
    return JSONResponse(status_code=422, content={"detail": errors})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cart_router)
app.include_router(restaurant_router)


@app.get(
    "/",
    response_model=HomeResponse,
    summary="API welcome message",
    description="Confirms Food Delivery API is running. No parameters.",
)
def home():
    return {"message": "Food Delivery Api is running"}


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Confirms API is running. No parameters, and returns status Ok",
)
def health_check():
    return {"status": "Ok"}

@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})