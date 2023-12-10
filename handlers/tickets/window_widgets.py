import operator
from typing import Any

from aiogram_dialog.widgets.kbd import Select, ScrollingGroup
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format

from aiogram.types import CallbackQuery, ContentType
from aiogram_dialog.dialog import DialogManager

from utils.dialog_categories import ticket_categories
from handlers.tickets.button_callbacks import ButtonCallbacks


async def on_ticket_subj_selected(callback: CallbackQuery, widget: Any,
                                  manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.answer(text="Немає категорій!")

    manager.dialog_data["subject"] = ticket_categories[int(item_id)]
    await manager.next()


class TelegramInputs:
    ticket_subj_select = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            id="select_subj",
            on_click=on_ticket_subj_selected,
            item_id_getter=operator.itemgetter(1),
            items="subjects"
        ),
        id="scroll_subj",
        height=6,
        width=1
    )

    input_description = MessageInput(
        func=ButtonCallbacks.process_description,
        content_types=ContentType.TEXT
    )


class TelegramBtns:
    pass
