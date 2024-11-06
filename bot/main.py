import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bestconfig import Config

BOT_TOKEN = "8086097440:AAFhdBiy7ZbLcfCBzMgTlsaGApkqJs_xvpk"
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())


@dp.message(F.text)
async def echo(message: types.Message):
    await message.reply(message.text)


async def main():
    print(BOT_TOKEN)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
