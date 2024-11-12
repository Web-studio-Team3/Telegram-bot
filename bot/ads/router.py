from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.config import redis_db
from typing import Any
from aiogram import F

ads_router = Router(name=__name__)


@ads_router.message(Command("test"))
async def message_handler(message: Message) -> Any:
    #print(redis_db.ping())
    #await message.answer("1")
    redis_db.set("test", f"{message.text}")
    await message.answer(redis_db.get("test"))
    redis_db.close()
