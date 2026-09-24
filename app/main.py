from fastapi import FastAPI
from app.api.routes.restaurants import router as restaurant_router

app = FastAPI()

app.include_router(restaurant_router)

@app.get("/")
def home():
    return{"message" : "Food Delivery Api is running"}

@app.get("/health")
def health_check():
    return{"status": "Ok"}
