"""Роутер с хендлерами для обхявления"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from config import redis_db
from typing import Any
from bot.ads.model import Ads
from bot.ads.inline_buttons import inl_keyboard

ads_router = Router(name=__name__)
storage = MemoryStorage()


@ads_router.message(Command("hh"))
async def message_handler(message: Message) -> Any:
    """
    Функция для создания объявления
    :param message:
    :return:
    """

    ads = Ads()

    ads.id = message.message_id
    ads.id_user = message.from_user.id
    await message.answer("Объявление будет Анонимным?", reply_markup=inl_keyboard)
    print(ads)
    # redis_db.set("test", f"{message.text}")
    # await message.answer(redis_db.get("test"))
    # redis_db.close()


@ads_router.callback_query(Command("/re"))
async def cmd_start(call: CallbackQuery, state: FSMContext):
    await message

# @ads_router.callback_query(func=lambda value: value.data == 'yes')
# async def yes_callback():
#     return "yes"
#
#
# @ads_router.callback_query(func=lambda value: value.data == 'no')
# async def no_callback():
#     return "no"
