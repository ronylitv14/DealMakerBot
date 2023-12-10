import operator
from typing import List, Any

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Multiselect, Select, Url

from .button_callbacks import ButtonCallbacks

from database.crud import get_orders, get_chats_by_taskid, UserType
from database.models import Task, Chat


async def on_order_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    orders: List[Task] = manager.dialog_data["orders"]

    user_type: UserType = manager.dialog_data.get("user_type")
    for order in orders:
        if order.task_id == int(item_id):
            builder = InlineKeyboardBuilder()
            chats: List[Chat] = await get_chats_by_taskid(order.task_id)
            for chat in chats:
                builder.add(
                    InlineKeyboardButton(
                        text=chat.group_name,
                        url=f"https://t.me/dealmakerchatbot?start=chat-{chat.id}" if user_type == UserType.client else chat.invite_link
                    )
                )

            await callback.message.answer(
                text=f"Посилання на чати!" if len(chats) >= 1 else "Для цього замовлення, на жаль, "
                                                                   "немає доступних посилань!",
                reply_markup=builder.as_markup()
            )
            return


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
