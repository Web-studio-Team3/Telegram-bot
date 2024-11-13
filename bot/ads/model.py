"""Модель данных для объявдения"""
from pydantic import BaseModel


class Ads(BaseModel):
    id: int
    id_user: str
    contact: str
    description: str
    photo: bytes
    price: int
    anonim: str
