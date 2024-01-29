from aiogram.types import ContentType
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from handlers.admin_panel.inactive_chat.button_callbacks import ButtonCallbacks


class TelegramInput:
    input_chat_id = MessageInput(
        func=ButtonCallbacks.process_chat_id,
        content_types=ContentType.TEXT
    )


class TelegramBtns:
    btn_accept_deactivation = Button(Const("Підтвердити"), id="btn_accept_da",
                                     on_click=ButtonCallbacks.accept_chat_deactivation)

    btn_reject_deactivation = Button(Const("Відмовити"), id="btn_reject_da",
                                     on_click=ButtonCallbacks.reject_chat_deactivation)
