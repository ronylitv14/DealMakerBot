
from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Back, Row

from database_api.components.tasks import TaskModel
from handlers.my_orders.window_widgets import (
    TelegramBtns,
    TelegramInputs
)

from handlers.my_orders.window_state import MyOrders
from database_api.components.tasks import TasksList


def create_valid_button(task: TaskModel):
    return f"№ замовлення {task.task_id}, Предмет: {task.subjects[0]}"


async def render_my_orders(**kwargs):
    dialog_manager = kwargs.get("dialog_manager")
    orders = dialog_manager.dialog_data.get("orders")

    updated_orders = []

    if isinstance(orders, TasksList):
        for ind, order in enumerate(orders):
            updated_orders.append((order, ind))

    return {
        "orders": updated_orders if updated_orders else [("У вас поки немає замовлень", -1)]
    }


main_window = Window(
    Const("Огляд ваших замовлень"),
    TelegramBtns.btn_active_orders,
    TelegramBtns.btn_finished_orders,
    Row(
        TelegramBtns.btn_cancel,
    ),
    state=MyOrders.main
)

showing_orders_window = Window(
    Const("Виведені усі замовлення"),
    TelegramInputs.input_active_orders,
    Row(
        Back(Const("Назад")),
        TelegramBtns.btn_cancel,
    ),
    state=MyOrders.watch_orders,
    parse_mode="HTML",
    getter=render_my_orders
)


async def set_starting_state(callback: CallbackQuery, manager: DialogManager):
    state_object: FSMContext = manager.dialog_data.get("state_obj")
    cur_state = manager.dialog_data.get("cur_state")
    if state_object:
        await state_object.set_state(cur_state)


def create_my_orders_dialog():
    return Dialog(
        main_window,
        showing_orders_window,
        on_close=set_starting_state
    )
