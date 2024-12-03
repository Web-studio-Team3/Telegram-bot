"""Main"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.ads.router import ads_router
from bot.items.router import item_router
from config import conf

BOT_TOKEN = conf.get("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())


async def main():
    """
    Входная функция

    :return: Диспатчер корректно запущен и принимает обновления с ТГ
    """
    dp.include_routers(
        item_router,
        ads_router
    )
    await dp.start_polling(bot, skip_updates=True)
    print("Succesfuly load!")

if __name__ == "__main__":
    """Точка входа"""
    asyncio.run(main())
