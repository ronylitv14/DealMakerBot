from aiogram_dialog.dialog import Dialog, DialogManager

from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Back, Row

from database_api.components.chats import ChatsList, Chats
from database_api.components.tasks import TaskModel, UserType
from handlers.my_orders.window_widgets import (
    TelegramBtns,
    TelegramInputs
)

from handlers.my_orders.window_state import MyOrders
from database_api.components.tasks import TasksList
from database_api.components.transactions import Transactions, TransactionList, TransactionType, TransactionStatus
from keyboards.inline_keyboards import create_aiogram_dialog_urls


def create_valid_button(task: TaskModel):
    return f"№ замовлення {task.task_id}, Предмет: {task.subjects[0]}"


async def render_my_orders(**kwargs):
    dialog_manager = kwargs.get("dialog_manager")
    orders = TasksList(**dialog_manager.dialog_data.get("orders"))

    updated_orders = []

    if isinstance(orders, TasksList):
        for ind, order in enumerate(orders):
            updated_orders.append((order, ind))

    return {
        "orders": updated_orders if updated_orders else [("У вас поки немає замовлень", -1)]
    }


async def get_order_links(**kwargs):
    dialog_manager: DialogManager = kwargs.get("dialog_manager")
    user_type: UserType = dialog_manager.dialog_data.get("user_type")
    task = TaskModel(**dialog_manager.dialog_data.get("order"))

    chats: ChatsList = await Chats().get_chats_by_task_id(
        task_id=task.task_id
    ).do_request()

    transaction: TransactionList = await Transactions().get_transaction_data(
        sender_id=task.client_id,
        receiver_id=task.executor_id,
        task_id=task.task_id,
        transaction_type=TransactionType.transfer,
        transaction_status=TransactionStatus.pending
    ).do_request()

    if isinstance(transaction, TransactionList):
        dialog_manager.dialog_data["transaction"] = transaction[0].model_dump(mode="json")
        dialog_manager.dialog_data["has_accept_offer"] = True

    if not isinstance(chats, ChatsList):
        dialog_manager.dialog_data["has_chats"] = False
        return {
            "urls": [("None", "https://youtube.com", -1)],
        }

    urls = create_aiogram_dialog_urls(chats, user_type)
    dialog_manager.dialog_data["has_chats"] = True

    return {
        "urls": urls,

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

order_details_window = Window(
    Const("Детальні дані щодо замовлення!"),
    TelegramBtns.btn_accept_order,
    TelegramInputs.list_chat_links,
    Row(
        Back(Const("Назад")),
        TelegramBtns.btn_cancel,
    ),
    state=MyOrders.order_details,
    parse_mode="HTML",
    getter=get_order_links
)

accept_execution_window = Window(
    Format("{dialog_data[task_msg]}"),
    TelegramBtns.btn_succeed_exec,
    Row(
        Back(Const("Назад")),
        TelegramBtns.btn_cancel,
    ),
    state=MyOrders.accept_task_execution
)


def create_my_orders_dialog():
    return Dialog(
        main_window,
        showing_orders_window,
        order_details_window,
        accept_execution_window
    )
