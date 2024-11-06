from pydantic import BaseModel


class Items(BaseModel):
    id: str
    category_id: str
    title: str
    description: str
    condition: str
    address: str
    cost: str
    status: str
    seller_id: str
