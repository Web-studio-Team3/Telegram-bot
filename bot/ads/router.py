"""Роутер с хендлерами для обхявления"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType
from aiogram.utils.chat_action import ChatActionSender

from config import redis_db
from typing import Any
from bot.ads.model import Ads
from bot.ads.inline_buttons import anonymity_buttons, draft_buttons, moderator_buttons

MODERATOR_CHAT_ID: int = -1002270311823
TELEGRAM_CHANNEL_ID: int = -1002319098987

ads_router: Router = Router(name=__name__)


def get_ad_from_redis(user_id: int) -> Ads:
    """
    Загружает объявление из Redis по ID пользователя.

    :param user_id: Идентификатор пользователя.
    :return: Объект объявления Ads.
    """
    redis_key = f"ad:{user_id}"
    ad_data = redis_db.hgetall(redis_key)
    ad = Ads()
    for key, value in ad_data.items():
        setattr(ad, key, value)
    return ad


def save_ad_to_redis(user_id: int, ad: Ads) -> None:
    """
    Сохраняет объект объявления в Redis.

    :param user_id: Идентификатор пользователя.
    :param ad: Объект объявления Ads.
    """
    redis_key = f"ad:{user_id}"

    ad_data = {key: (value if value is not None else "") for key, value in vars(ad).items()}
    redis_db.hset(redis_key, mapping=ad_data)


@ads_router.message(Command("start_ad"))
async def start_ad_creation(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start_ad. Начинает процесс создания объявления.

    :param message: Объект сообщения.
    :param state: Контекст конечного автомата.
    """
    user_id = message.from_user.id
    ad = Ads(id_user=user_id)
    save_ad_to_redis(user_id, ad)

    await message.answer(
        "Будет ли объявление анонимным?",
        reply_markup=anonymity_buttons(),
    )


@ads_router.callback_query(lambda call: call.data in ["anonymous_yes", "anonymous_no"])
async def set_anonymity(call: CallbackQuery, state: FSMContext) -> None:
    """
    Устанавливает анонимность объявления.

    :param call: Объект CallbackQuery.
    :param state: Контекст конечного автомата.
    """
    user_id = call.from_user.id
    ad = get_ad_from_redis(user_id)

    ad.anonim = "yes" if call.data == "anonymous_yes" else "no"
    ad.contact = f"@{call.from_user.username}" if call.from_user.username else "Не указано"

    message_text = (
        f"Ваше объявление будет анонимным. Модераторам доступен ваш контакт: {ad.contact}.\n"
        if ad.anonim == "yes" else
        f"Ваше объявление будет публичным с указанием контакта: {ad.contact}.\n"
    )
    await call.message.answer(message_text + "Пожалуйста, отправьте текст объявления.")

    save_ad_to_redis(user_id, ad)
    await state.set_state("ad_text")


@ads_router.message()
async def handle_message(message: Message, state: FSMContext) -> None:
    """
    Универсальный обработчик сообщений на основе текущего состояния.

    :param message: Объект сообщения.
    :param state: Контекст конечного автомата.
    """
    current_state = await state.get_state()

    if not current_state:
        await message.answer("Ошибка! Начните с команды /start_ad.")
        return

    handlers = {
        "ad_text": handle_text,
        "ad_photo": handle_photo,
        "ad_price": handle_price,
    }

    handler = handlers.get(current_state)
    if handler:
        await handler(message, state)


async def handle_text(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает текст объявления.

    :param message: Объект сообщения.
    :param state: Контекст конечного автомата.
    """
    user_id = message.from_user.id
    ad = get_ad_from_redis(user_id)

    ad.description = message.text.strip()
    save_ad_to_redis(user_id, ad)

    await message.answer("Текст объявления сохранён. Теперь отправьте фотографию.")
    await state.set_state("ad_photo")


async def handle_photo(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает фотографию объявления.

    :param message: Объект сообщения.
    :param state: Контекст конечного автомата.
    """
    if message.content_type != ContentType.PHOTO:
        await message.answer("Пожалуйста, отправьте фотографию.")
        return

    user_id = message.from_user.id
    ad = get_ad_from_redis(user_id)

    ad.photo = message.photo[-1].file_id
    save_ad_to_redis(user_id, ad)

    await message.answer("Фотография сохранена. Укажите цену.")
    await state.set_state("ad_price")


async def handle_price(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает цену объявления.

    :param message: Объект сообщения.
    :param state: Контекст конечного автомата.
    """
    if not message.text.isdigit():
        await message.answer("Цена должна быть числом.")
        return

    user_id = message.from_user.id
    ad = get_ad_from_redis(user_id)

    ad.price = int(message.text)
    save_ad_to_redis(user_id, ad)

    await message.answer("Цена сохранена. Объявление завершено.")
    await show_draft(ad, message)
    await state.clear()


async def show_draft(ad: Ads, message: Message) -> None:
    """
    Показывает черновик объявления с кнопками редактирования.

    :param ad: Объект объявления.
    :param message: Объект сообщения.
    """
    draft_message = (
        f"Ваше объявление:\n\n"
        f"Текст: {ad.description}\n"
        f"Цена: {ad.price}\n"
        f"{'Анонимное' if ad.anonim == 'yes' else f'Контакт: {ad.contact}'}"
    )
    await message.answer(draft_message, reply_markup=draft_buttons())


@ads_router.callback_query(lambda call: call.data == "edit_text")
async def edit_text_start(call: CallbackQuery, state: FSMContext) -> None:
    """
    Переводит пользователя в состояние редактирования текста объявления.
    """
    await call.message.answer("Введите новый текст объявления:")
    await state.set_state("ad_text")
    await call.answer()


@ads_router.callback_query(lambda call: call.data == "edit_photo")
async def edit_photo_start(call: CallbackQuery, state: FSMContext) -> None:
    """
    Переводит пользователя в состояние редактирования фото объявления.
    """
    await call.message.answer("Отправьте новое фото для объявления:")
    await state.set_state("ad_photo")
    await call.answer()


@ads_router.callback_query(lambda call: call.data == "edit_price")
async def edit_price_start(call: CallbackQuery, state: FSMContext) -> None:
    """
    Переводит пользователя в состояние редактирования цены объявления.
    """
    await call.message.answer("Введите новую цену для объявления:")
    await state.set_state("ad_price")
    await call.answer()


@ads_router.callback_query(lambda call: call.data == "confirm_draft")
async def confirm_draft(call: CallbackQuery) -> None:
    """
    Подтверждает черновик и отправляет объявление на модерацию.

    :param call: Объект CallbackQuery.
    """
    user_id = call.from_user.id
    ad = get_ad_from_redis(user_id)

    await send_to_moderators(ad, call.message)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Ваше объявление отправлено на модерацию.")
    await call.answer()


async def send_to_moderators(ad: Ads, message: Message) -> None:
    """
    Отправляет объявление модераторам.

    :param ad: Объект объявления.
    :param message: Объект сообщения.
    """
    moderation_message = (
        f"Новое объявление на модерации:\n"
        f"Текст: {ad.description}\n"
        f"Цена: {ad.price}\n"
        f"{'Анонимное' if ad.anonim == 'yes' else f'Контакт: {ad.contact}'}"
    )
    await message.bot.send_photo(
        MODERATOR_CHAT_ID,
        photo=ad.photo,
        caption=moderation_message,
        reply_markup=moderator_buttons(ad.id_user),
    )


@ads_router.callback_query(lambda call: call.data.startswith("approve_"))
async def approve_ad(call: CallbackQuery) -> None:
    """
    Обработчик одобрения объявления модератором.
    Публикует объявление в Telegram-канал и уведомляет пользователя.

    :param call: Объект CallbackQuery.
    """
    user_id = int(call.data.split("_")[1])
    ad = get_ad_from_redis(user_id)

    await publish_to_channel(ad, call.message.bot)

    await call.message.edit_caption(
        caption=f"{call.message.caption}\n\n✅ <b>Одобрено</b>",
        parse_mode="HTML",
        reply_markup=None
    )

    await call.message.bot.send_message(
        chat_id=user_id,
        text="Ваше объявление одобрено модератором и опубликовано в канале."
    )
    await call.answer("Объявление одобрено.")


async def publish_to_channel(ad: Ads, bot) -> None:
    """
    Публикует объявление в Telegram-канале.

    :param ad: Объект объявления.
    :param bot: Экземпляр бота.
    """
    channel_message = (
        f"📢 <b>Новое объявление:</b>\n\n"
        f"📝 <b>Текст:</b> {ad.description}\n"
        f"💰 <b>Цена:</b> {ad.price} руб.\n"
        f"{'🙈 Анонимное объявление' if ad.anonim == 'yes' else f'📞 Контакт: {ad.contact}'}"
    )
    await bot.send_photo(
        chat_id=TELEGRAM_CHANNEL_ID,
        photo=ad.photo,
        caption=channel_message,
        parse_mode="HTML"
    )


@ads_router.callback_query(lambda call: call.data.startswith("reject_"))
async def reject_ad(call: CallbackQuery) -> None:
    """
    Обработчик отклонения объявления модератором.
    Уведомляет пользователя об отказе и обновляет сообщение в чате модераторов.

    :param call: Объект CallbackQuery.
    """
    user_id = int(call.data.split("_")[1])

    # Обновление сообщения в чате модераторов
    await call.message.edit_caption(
        caption=f"{call.message.caption}\n\n❌ <b>Отклонено</b>",
        parse_mode="HTML",
        reply_markup=None
    )

    await call.message.bot.send_message(
        chat_id=user_id,
        text="Ваше объявление отклонено модератором."
    )
    await call.answer("Объявление отклонено.")

# storage = MemoryStorage()
#
#
# @ads_router.message(Command("hh"))
# async def message_handler(message: Message) -> Any:
#     """
#     Функция для создания объявления
#     :param message:
#     :return:
#     """
#
#     ads = Ads()
#
#     ads.id = message.message_id
#     ads.id_user = message.from_user.id
#     await message.answer("Объявление будет Анонимным?", reply_markup=inl_keyboard)
#     print(ads)
#     redis_db.set("test", f"{message.text}")
#     await message.answer(redis_db.get("test"))
#     redis_db.close()


# @ads_router.callback_query(Command("/re"))
# async def cmd_start(call: CallbackQuery, state: FSMContext):
#     await message

# @ads_router.callback_query(func=lambda value: value.data == 'yes')
# async def yes_callback():
#     return "yes"
#
#
# @ads_router.callback_query(func=lambda value: value.data == 'no')
# async def no_callback():
#     return "no"
