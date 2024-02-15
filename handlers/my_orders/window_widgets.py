import operator
from typing import Any

from magic_filter import F
from aiogram.types import CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.text import Const, Format, Case
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Url, ListGroup, Cancel, Back

from handlers.my_orders.button_callbacks import ButtonCallbacks, AcceptSuccessExecution


async def on_order_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer("Немає доступних замовлень!")

    orders = manager.dialog_data.get("orders")
    manager.dialog_data["order"] = orders["list_values"][int(item_id)]
    manager.dialog_data["has_accept_offer"] = False
    await manager.next()


class TelegramInputs:
    select_active_orders = Select(
        text=Format("{item[0]}"),
        id="select_orders",
        item_id_getter=operator.itemgetter(1),
        items="orders",
        on_click=on_order_selected
    )

    input_active_orders = ScrollingGroup(
        select_active_orders,
        height=5,
        width=1,
        id="scroll_orders"
    )

    list_chat_links = ListGroup(
        Url(Format("{item[0]}"), Format("{item[1]}")),
        items="urls",
        id='ls_chat_links',
        item_id_getter=operator.itemgetter(2),
        when=F["dialog_data"]["has_chats"]
    )


class TelegramBtns:
    btn_active_orders = Button(Const("Переглянути активні замовлення"), id="b_active_orders",
                               on_click=ButtonCallbacks.get_active_orders)
    btn_finished_orders = Button(Const("Завершені завдання"), id='b_finished_orders',
                                 on_click=ButtonCallbacks.get_finished_orders)
    btn_cancel = Button(Const("Вийти"), id="b_cancel", on_click=ButtonCallbacks.cancel_dialog)
    btn_accept_order = Button(Const("Підтвердження замовлення"), id="b_accept",
                              on_click=ButtonCallbacks.navigate_to_acceptance_window,
                              when=F["dialog_data"]["has_accept_offer"])

    btn_succeed_exec = Button(Const("Підтвердити"), id="b_succeed_exec",
                              on_click=AcceptSuccessExecution.accept_success_execution_callback)
