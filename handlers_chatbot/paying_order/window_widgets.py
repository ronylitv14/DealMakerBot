from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import MessageInput

from aiogram.enums import ContentType
from handlers_chatbot.paying_order.button_callbacks import ButtonCallbacks, InputCallbacks


class TelegramInputs:
    input_offer_price = MessageInput(
        func=InputCallbacks.process_offer_price,
        content_types=ContentType.TEXT
    )


class TelegramBtns:
    btn_accept_price = Button(Const("Прийняти"), id="btn_accept_price", on_click=ButtonCallbacks.accept_price)
    btn_reject_price = Button(Const("Відхилити"), id="btn_reject_price", on_click=ButtonCallbacks.reject_price)
