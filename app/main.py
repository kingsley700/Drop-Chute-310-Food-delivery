from fastapi import FastAPI
from app.api.routes.restaurants import router as restaurant_router
from app.schemas.health import HealthResponse
from app.schemas.home import HomeResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

app.include_router(restaurant_router)

@app.get(
    "/",
    response_model = HomeResponse,
    summary = "API welcome message",
    description = "Confirms Food Delivery API is running. No parameters."
)

def home():
    return{"message" : "Food Delivery Api is running"}


@app.get("/health", response_model=HealthResponse,
        summary="Health check",
        description = "Confirms API is running. No parameters, and returns status Ok")

def health_check():
    return{"status": "Ok"}


