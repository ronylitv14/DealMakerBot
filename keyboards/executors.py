from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from .keyboard_fields import ExecutorKeyboard


def create_keyboard_executor():
    builder = ReplyKeyboardBuilder()

    builder.row(
        types.KeyboardButton(text=ExecutorKeyboard.my_orders),
        types.KeyboardButton(text=ExecutorKeyboard.profile_instruments),
    )

    builder.row(
        types.KeyboardButton(text=ExecutorKeyboard.new_deal),
        types.KeyboardButton(text=ExecutorKeyboard.balance),
    )

    builder.row(
        types.KeyboardButton(text=ExecutorKeyboard.client_profile)
    )

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)
