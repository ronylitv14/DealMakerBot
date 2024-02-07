import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select

from handlers.my_orders.button_callbacks import ButtonCallbacks
from keyboards.inline_keyboards import create_chats_inline_kbd

from database_api.components.tasks import Tasks, TaskModel, UserType, TasksList
from database_api.components.chats import Chats, ChatsList
from dotenv import load_dotenv

load_dotenv()


async def on_order_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer("Немає доступних замовлень!")

    user_type: UserType = manager.dialog_data.get("user_type")
    orders = TasksList(**manager.dialog_data.get("orders"))
    order: TaskModel = orders[int(item_id)]

    chats: ChatsList = await Chats().get_chats_by_task_id(
        task_id=order.task_id
    ).do_request()

    if not isinstance(chats, ChatsList):
        return await callback.message.answer("Поки немає доступних чатів для цього замовлення!")

    reply_markup = create_chats_inline_kbd(chats, user_type)

    await callback.message.answer(
        text=f"Посилання на чати!" if len(chats) >= 1 else "Для цього замовлення, на жаль, "
                                                           "немає доступних посилань!",
        reply_markup=reply_markup
    )


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


class TelegramBtns:
    btn_active_orders = Button(Const("Переглянути активні замовлення"), id="b_active_orders",
                               on_click=ButtonCallbacks.get_active_orders)
    btn_finished_orders = Button(Const("Завершені завдання"), id='b_finished_orders',
                                 on_click=ButtonCallbacks.get_finished_orders)
    btn_cancel = Button(Const("Вийти"), id="b_cancel", on_click=ButtonCallbacks.cancel_dialog)
