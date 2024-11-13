"""Роутер с хендлерами для Товара"""
from aiogram import Router
from aiogram import types, F

item_router = Router()


@item_router.message(F.text)
async def get_user_text(message: types.Message):
    if message.text == "Привет":
        await message.reply("Привет, я балванка")
    else:
        await message.reply("Сорри, но я тебя не понял")
