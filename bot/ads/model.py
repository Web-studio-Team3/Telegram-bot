"""Модель данных для объявдения"""
#from pydantic import BaseModel
from typing import Optional


class Ads:
    id: Optional[int] = None
    id_user: Optional[str] = None
    contact: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[bytes] = None
    price: Optional[int] = None
    anonim: Optional[str] = None

    def __init__(
            self,
            id: Optional[int] = None,
            id_user: Optional[str] = None,
            contact: Optional[str] = None,
            description: Optional[str] = None,
            photo: Optional[bytes] = None,
            price: Optional[int] = None,
            anonim: Optional[str] = None,
    ):
        self.id = id
        self.id_user = id_user
        self.contact = contact
        self.description = description
        self.photo = photo
        self.price = price
        self.anonim = anonim

    def __str__(self):
        return f"id: {self.id}\nid_user: {self.id_user}\ncontact: {self.contact}\ndescription: { self.description}\n photo: {self.photo}\nanonim: {self.anonim}"
    # def __init__(self):
    #     self.id = 1
    #     self.id_user = "m"
    #     self.contact = "1"
    #     self.description= "1"
    #     self.photo = bytes("010101")
    #     self.anonim = "1"
