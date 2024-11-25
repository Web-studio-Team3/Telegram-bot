"""Модель для товара"""
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

    def __str__(self):
        return (
            f"🔹 <b>Название:</b> {self.title}\n"
            f"🔹 <b>Описание:</b> {self.description}\n"
            f"🔹 <b>Контакт:</b> {self.address}\n"
            f"🔹 <b>Цена:</b> {self.cost} ₽"
        )