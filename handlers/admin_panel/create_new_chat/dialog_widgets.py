import operator
from typing import Any

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select, ScrollingGroup
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.dialog import DialogManager

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery

from handlers.admin_panel.create_new_chat.button_callbacks import InputCallback, SelectCallbacks, ButtonCallbacks


def create_message_input(custom_func):
    return MessageInput(
        func=custom_func,
        content_types=ContentType.TEXT
    )


def create_scrolling_group(select_func, items_name, width: int = 1):
    return ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            on_click=select_func,
            item_id_getter=operator.itemgetter(1),
            items=items_name,
            id=f"s_query_{items_name}"
        ),
        height=6,
        width=width,
        id=f"sg_query_{items_name}"
    )


class TelegramInputs:
    input_query_exec = create_message_input(
        InputCallback.process_query_input_executor
    )

    input_desc = create_message_input(
        InputCallback.process_description
    )

    input_query_client = create_message_input(
        InputCallback.process_query_input_client
    )

    select_executor = create_scrolling_group(
        SelectCallbacks.on_executor_selected,
        items_name="executors"
    )

    select_client = create_scrolling_group(
        SelectCallbacks.on_client_selected,
        items_name="clients"
    )

    select_subject = create_scrolling_group(
        SelectCallbacks.on_subject_selected,
        items_name="subjects",
        width=2
    )


class TelegramBtns:
    btn_accept_deals = Button(Format("Створити чат"), id="b_create_chat", on_click=ButtonCallbacks.create_deal_for_all)

