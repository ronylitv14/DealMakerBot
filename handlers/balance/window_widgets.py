import operator
from typing import Any

from aiogram_dialog.widgets.kbd import ManagedCounter
from aiogram.types import CallbackQuery
from aiogram.enums import ContentType

from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Start, Back, Select, Column
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput

from .button_callbacks import ButtonCallbacks
from .window_state import WithdrawingMoneySub


async def on_card_selected(callback: CallbackQuery, widget: Select,
                           manager: DialogManager, item_id: str):
    if item_id != "0":
        await callback.answer(
            text="Обрано карту!"
        )
        upd_cards = manager.dialog_data.get("updated_cards")
        manager.dialog_data["withdrawal_card"] = upd_cards[int(item_id) - 1][0]
        await manager.switch_to(WithdrawingMoneySub.accept_withdraw)
    else:
        print(manager.dialog_data)

        await callback.answer(
            text="Карток немає"
        )


class TelegramInputs:
    select_card = Column(
        Select(
            text=Format("{item[0]}"),
            id="s_card",
            items="cards",
            item_id_getter=operator.itemgetter(1),
            on_click=on_card_selected
        )
    )

    input_money = MessageInput(
        func=ButtonCallbacks.process_money_adding,
        content_types=ContentType.TEXT
    )

    input_password = MessageInput(
        func=ButtonCallbacks.check_password,
        content_types=ContentType.TEXT
    )

    input_sum = MessageInput(
        func=ButtonCallbacks.process_sum_input,
        content_types=ContentType.TEXT
    )

    input_card = MessageInput(
        func=ButtonCallbacks.process_card_input,
        content_types=ContentType.TEXT
    )


class TelegramBtns:
    btn_add_money = Button(Const("Додати кошти"), id="b_add", on_click=ButtonCallbacks.add_money)
    btn_withdraw_money = Start(Const("Вивести кошти"), id="b_withdraw", state=WithdrawingMoneySub.checking_password)
    btn_accept_deposit = Button(Const("Підтвердити"), id="b_accept_d", on_click=ButtonCallbacks.accept_deposit)
    btn_back = Back(Const("Назад"), id="b_back")
    btn_cancel = Button(Const("Відмінити"), id="b_cancel", on_click=ButtonCallbacks.cancel_balance_dialog)
    btn_cancel_subdialog = Button(Const("Відмінити"), id="b_cancel_sub", on_click=ButtonCallbacks.cancel_subdialog)
    btn_accept_withdraw = Button(Const("Підтвердити"), id="b_accept_w", on_click=ButtonCallbacks.accept_withdraw)
