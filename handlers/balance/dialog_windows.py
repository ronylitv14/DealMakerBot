from typing import Any, Dict

from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.dialog import DialogManager, Dialog

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from handlers.balance.window_state import BalanceGroup, WithdrawingMoneySub
from handlers.balance.window_widgets import (
    TelegramBtns,
    TelegramInputs
)
from utils.bank_card_utils import format_card_number
from utils.dialog_texts import (
    adding_money_text,
    balance_text,
    accepting_payment,
    check_password_text,
    input_sum_text,
    choose_card_text,
    accepting_withdraw_text
)

main_window = Window(
    Format(balance_text),
    TelegramBtns.btn_add_money,
    TelegramBtns.btn_withdraw_money,
    TelegramBtns.btn_cancel,
    state=BalanceGroup.main_window,
    parse_mode="HTML"
)

adding_money_window = Window(
    Format(adding_money_text),
    TelegramInputs.input_money,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel,
    ),
    state=BalanceGroup.adding_money,
    parse_mode="HTML"
)

accepting_request_window = Window(
    Format(accepting_payment),
    TelegramBtns.btn_accept_deposit,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel,
    ),
    state=BalanceGroup.accept_request,
    parse_mode="HTML"
)

checking_password_window = Window(
    Const(check_password_text),
    TelegramInputs.input_password,
    Row(
        TelegramBtns.btn_cancel_subdialog,
    ),
    state=WithdrawingMoneySub.checking_password,
    parse_mode="HTML"
)

withdraw_money_window = Window(
    Format(input_sum_text),
    TelegramInputs.input_sum,
    TelegramBtns.btn_withdraw_all_money,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel_subdialog,
    ),
    state=WithdrawingMoneySub.withdraw_sum,
    parse_mode="HTML"
)


async def get_cards_info(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    cards = manager.dialog_data.get("cards")

    updated_cards = []

    for ind, card in enumerate(cards):
        updated_cards.append((format_card_number(card), ind))

    manager.dialog_data["updated_cards"] = updated_cards

    return {
        "cards": updated_cards if updated_cards else [("Немає карток", -1)]
    }


adding_card_window = Window(
    Const(choose_card_text),
    TelegramInputs.select_card,
    TelegramInputs.input_card,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel_subdialog,
    ),
    state=WithdrawingMoneySub.handle_cards,
    getter=get_cards_info,
    parse_mode="HTML"
)

accept_card_window = Window(
    Format(accepting_withdraw_text),
    TelegramBtns.btn_accept_withdraw,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel_subdialog,
    ),
    state=WithdrawingMoneySub.accept_withdraw,
    parse_mode="HTML"
)


# async def close_balance_dialog(data: Any, manager: DialogManager):
#     state: FSMContext = manager.dialog_data.get("state_object")
#     cur_state: State = manager.dialog_data.get("cur_state")
#     if state:
#         await state.set_state(cur_state)
#
#
# async def on_process_result(start_data, result: Dict[str, str],
#                             dialog_manager: DialogManager):
#
#     if result.get("has_ended"):
#         await dialog_manager.done()


def create_balance_dialogs():
    return (
        Dialog(
            main_window,
            adding_money_window,
            accepting_request_window,
            # on_close=close_balance_dialog,
            # on_process_result=on_process_result
        ),
        Dialog(
            checking_password_window,
            withdraw_money_window,
            adding_card_window,
            accept_card_window
        )
    )
