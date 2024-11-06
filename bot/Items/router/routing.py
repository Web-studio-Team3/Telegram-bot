
from aiogram import Bot, Dispatcher, types, F
from bot.main import dp


@dp.message(F.text)
async def get_user_text(message: types.Message):
    if message.text == "Привет":
        await message.reply("Привет, я балванка")
    else:
        await message.reply("Сорри, но я тебя не понял")
