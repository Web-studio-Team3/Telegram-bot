from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# inl_yes = InlineKeyboardButton(text="Да", callback_data="yes")
# inl_no = InlineKeyboardButton(text="Нет", callback_data="no")
#
# inline_buttons = [[inl_yes, inl_no]]
#
# inl_keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)


def anonymity_buttons() -> InlineKeyboardMarkup:
    """
    Создает кнопки для выбора анонимности объявления.

    :return: Объект InlineKeyboardMarkup.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="anonymous_yes")],
            [InlineKeyboardButton(text="Нет", callback_data="anonymous_no")],
        ]
    )


def finish_photos_button() -> InlineKeyboardMarkup:
    """
    Создает кнопку для завершения добавления фотографий.

    :return: Объект InlineKeyboardMarkup.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Завершить добавление фото", callback_data="finish_photos")],
        ]
    )


def draft_buttons() -> InlineKeyboardMarkup:
    """
    Создает кнопки для работы с черновиком объявления.

    :return: Объект InlineKeyboardMarkup.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Редактировать текст", callback_data="edit_text"),
                InlineKeyboardButton(text="📷 Редактировать фото", callback_data="edit_photo"),
            ],
            [
                InlineKeyboardButton(text="💰 Редактировать цену", callback_data="edit_price"),
                InlineKeyboardButton(text="✅ Отправить на модерацию", callback_data="confirm_draft"),
            ],
        ]
    )


def moderator_buttons(user_id: int) -> InlineKeyboardMarkup:
    """
    Создает кнопки для модерации объявления.

    :param user_id: ID пользователя.
    :return: Объект InlineKeyboardMarkup.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}"),
            ]
        ]
    )

