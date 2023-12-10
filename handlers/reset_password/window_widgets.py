from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from .button_callbacks import ButtonCallbacks


class TelegramInputs:
    pass


class TelegramBtns:
    btn_mobile = Button(Const("Відновити за номером телефону"), id="b_mobile",
                        on_click=ButtonCallbacks.get_token_by_mobile)
    btn_email = Button(Const("Відновити за поштою"), id="b_email", on_click=ButtonCallbacks.get_token_by_email)
    btn_cancel = Button(Const("Відмінити"), id="b_cancel", on_click=ButtonCallbacks.cancel_dialog)
