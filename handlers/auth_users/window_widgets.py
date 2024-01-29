from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Next
from aiogram_dialog.widgets.text import Const
from aiogram.enums.content_type import ContentType

from handlers.auth_users.button_callbacks import ButtonCallbacks


class TelegramInputs:
    input_username = MessageInput(
        content_types=ContentType.TEXT,
        func=ButtonCallbacks.process_username
    )

    input_email = MessageInput(
        content_types=ContentType.TEXT,
        func=ButtonCallbacks.process_email
    )

    input_password = MessageInput(
        content_types=ContentType.TEXT,
        func=ButtonCallbacks.process_password
    )

    input_confirm_password = MessageInput(
        content_types=ContentType.TEXT,
        func=ButtonCallbacks.save_user_data
    )


class TelegramButtons:
    btn_back = Back(Const("Назад"))
    btn_cancel = Button(Const("Відмінити"), id="id_cancel", on_click=ButtonCallbacks.cancel_auth)
    btn_skip = Next(Const("Пропустити"), id="id_skip")
