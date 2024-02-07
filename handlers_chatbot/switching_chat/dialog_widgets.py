import operator
from typing import Any

from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, ScrollingGroup
from aiogram_dialog.widgets.text import Format

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database_api.components.chats import ChatsList


async def on_chat_selected(callback: CallbackQuery, widget: Any,
                           manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer("Немає чатів!")

    builder = InlineKeyboardBuilder()

    chats = ChatsList(**manager.start_data.get("chats"))
    chat = chats[int(item_id)]

    builder.add(
        InlineKeyboardButton(
            text="Розпочати чат",
            callback_data=f"chat-start|{chat.id}"
        )
    )

    await callback.message.answer(
        text="<b>Увага!</b> Коли ви натиснете кнопку розпочати чат - зможете розпочати діалог з виконавцем",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )

    await manager.done()

select_chat = ScrollingGroup(
    Select(
        text=Format("{item[0]}"),
        item_id_getter=operator.itemgetter(1),
        on_click=on_chat_selected,
        items="chats",
        id="s_chats",
    ),
    id="sc_chats",
    height=5,
    width=1
)
