from aiogram_dialog.dialog import Dialog
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Row, Cancel

from handlers_chatbot.paying_order.window_states import PriceOffer, PriceOfferAccept
from handlers_chatbot.paying_order.window_widgets import TelegramBtns, TelegramInputs

offer_price_window = Window(
    Format("Запропонуйте тепер ціну для клієнта!"),
    TelegramInputs.input_offer_price,
    Cancel(Format("Відмінити")),
    state=PriceOffer.offer_price
)

accept_price = Window(
    Format("Прийміть ціну від виконавця!"),
    Row(
        TelegramBtns.btn_accept_price,
        TelegramBtns.btn_reject_price
    ),
    state=PriceOfferAccept.accept_price
)


def create_offer_dialog():
    return Dialog(
        offer_price_window
    ), Dialog(
        accept_price
    )
