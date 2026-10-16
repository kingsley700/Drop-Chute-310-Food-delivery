from pydantic import BaseModel

class HomeResponse(BaseModel):
    message: str