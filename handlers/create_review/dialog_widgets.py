import operator
from typing import Any

from aiogram.types import CallbackQuery, ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Group, ScrollingGroup, Multiselect, ManagedMultiselect, Cancel, Back, \
    Next, Button
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format, Const

from handlers.create_review.button_callbacks import ButtonCallbacks
from utils.dialog_categories import positive_aspects, negative_aspects


async def on_rating_clicked(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    manager.dialog_data["rating"] = int(item_id)
    await manager.next()


async def on_state_positives_changed(callback: CallbackQuery, widget: Multiselect, manager: DialogManager, *args, **kwargs):
    checked_items = widget.get_checked()
    manager.dialog_data["positives"] = [positive_aspects[int(ind)] for ind in checked_items]


async def on_state_negatives_changed(callback: CallbackQuery, widget: Multiselect, manager: DialogManager, *args, **kwargs):
    checked_items = widget.get_checked()
    manager.dialog_data["negatives"] = [negative_aspects[int(ind)] for ind in checked_items]


class TelegramWidgets:
    input_rating = Group(
        Select(
            text=Format("{item[0]}"),
            on_click=on_rating_clicked,
            id="s_rating",
            item_id_getter=operator.itemgetter(1),
            items="ratings",

        ),
        id="gs_ratings",
        width=1
    )

    input_comment = MessageInput(
        func=ButtonCallbacks.process_comment_and_dialog_end,
        content_types=ContentType.TEXT
    )


class ScrollingSights:
    input_positives = ScrollingGroup(
        Multiselect(
            Format("👤 {item[0]}"),
            Format("{item[0]}"),
            item_id_getter=operator.itemgetter(1),
            items="positives",
            id="ms_positives",
            on_state_changed=on_state_positives_changed
        ),
        id="sg_positives",
        width=1,
        height=8
    )

    input_negatives = ScrollingGroup(
        Multiselect(
            Format("‼ {item[0]}"),
            Format("{item[0]}"),
            item_id_getter=operator.itemgetter(1),
            items="negatives",
            id="ms_negatives",
            on_state_changed=on_state_negatives_changed
        ),
        id="sg_negatives",
        height=8,
        width=1
    )


def create_cancel_button(text: str):
    return Cancel(Const(text))


def create_back_button(text: str):
    return Back(Const(text))


def create_skip_button(text: str):
    return Next(Const(text))


class TelegramBtns:
    btn_save_dialog = Button(Const("Зберегти відгук"), id="b_end_dialog", on_click=ButtonCallbacks.end_dialog)
