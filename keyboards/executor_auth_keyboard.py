from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_keyboard_executor_auth():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text="Прийняти",
            callback_data="accept_executor"
        ),
        types.InlineKeyboardButton(
            text="Відмовити",
            callback_data="reject_executor"
        )
    )

    return builder.as_markup()
