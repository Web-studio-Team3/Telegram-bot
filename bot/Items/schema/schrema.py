from pydantic import BaseModel

class Ads(BaseModel):
    id: int
    contact: str
    description: str
    photo: bytes
    price: int