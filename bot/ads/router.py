from aiogram import Router
from aiogram.types import Message

ads = Router(name=__name__)


@ads.message()
async def message_handler(message: Message) -> Any:
    await message.answer('Hello from my router!')