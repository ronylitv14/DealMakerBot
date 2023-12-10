from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.state import State

from .keyboard_fields import KeyboardFields, ClientKeyboard, ProfileKeyBoard


def create_keyboard_client(kbd_field: type(KeyboardFields) = ClientKeyboard):
    builder = ReplyKeyboardBuilder()

    builder.row(

        types.KeyboardButton(text=kbd_field.create_order),
        types.KeyboardButton(text=kbd_field.profile_instruments)

    )

    builder.row(
        types.KeyboardButton(text=kbd_field.my_orders),
        types.KeyboardButton(text=kbd_field.instruction)
    )

    builder.row(
        types.KeyboardButton(text=kbd_field.new_deal),
        types.KeyboardButton(text=kbd_field.balance)
    )

    builder.row(
        types.KeyboardButton(text=kbd_field.executor_profile)
    )

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def create_profile_instruments():
    builder = ReplyKeyboardBuilder()

    builder.row(
        types.KeyboardButton(text=ProfileKeyBoard.edit_phone),
        types.KeyboardButton(text=ProfileKeyBoard.edit_name)
    )

    builder.row(
        types.KeyboardButton(text=ProfileKeyBoard.edit_email),
        types.KeyboardButton(text=ProfileKeyBoard.edit_password)
    )

    builder.row(
        types.KeyboardButton(text=ProfileKeyBoard.delete_account),
        types.KeyboardButton(text=ProfileKeyBoard.back)
    )

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)
