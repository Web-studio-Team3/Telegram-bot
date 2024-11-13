from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inl_yes = InlineKeyboardButton(text="Да", callback_data="yes")
inl_no = InlineKeyboardButton(text="Нет", callback_data="no")

inline_buttons = [[inl_yes, inl_no]]

inl_keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
