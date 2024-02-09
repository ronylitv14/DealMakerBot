from aiogram_dialog.widgets.text import Format
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Row

from .window_widgets import (
    TelegramInputs,
    TelegramBtns
)
from utils.dialog_texts import description_text, adding_materials_text, price_text, deadline_text

from .window_state import OrderState
from utils.dialog_categories import university_tasks, subject_titles
from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const

from handlers.utils.custom_widgets import SwitchInlineQueryCurrentChat


async def get_subjects(**kwargs):
    updated_subjects = []

    for ind, subject in enumerate(subject_titles):
        updated_subjects.append((subject, ind))

    return {
        "university_subjects": updated_subjects,
        "count": len(updated_subjects)
    }


async def get_order_type(**kwargs):
    updated_types = []

    for ind, subject in enumerate(university_tasks):
        updated_types.append((subject, ind))

    return {
        "university_tasks": updated_types,
        "count": len(updated_types),
    }


main_window = Window(
    Const("Потрібно відміти теги для вашого завдання"),
    TelegramInputs.order_type_select,
    Row(
        TelegramBtns.btn_cancel,
        TelegramBtns.btn_task_type
    ),
    state=OrderState.main,
    getter=get_order_type,
)

select_subject_window = Window(
    Const("Потрібно обрати предмет виконання"),
    TelegramInputs.subject_title_select,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel,
        TelegramBtns.btn_subject,
    ),
    SwitchInlineQueryCurrentChat(
        Const("Пошук за словами"),
        Const("Інше")
    ),
    TelegramInputs.input_subject,

    state=OrderState.adding_subjects,
    getter=get_subjects,
    parse_mode="HTML"
)

price_window = Window(
    Const(price_text),
    TelegramInputs.input_price,
    TelegramBtns.btn_set_unknown_price,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel
    ),
    state=OrderState.creating_price,
    parse_mode="HTML"
)

input_deadline_window = Window(
    Const(deadline_text),
    TelegramInputs.input_deadline,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel
    ),
    state=OrderState.deadline,
    parse_mode="HTML"
)

input_description_window = Window(
    Format(description_text),
    TelegramInputs.input_desc,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel

    ),
    state=OrderState.adding_description,
    parse_mode="HTML"

)

materials_window = Window(
    Const(adding_materials_text),
    TelegramInputs.input_docs,
    Row(
        TelegramBtns.btn_back,
    ),
    Row(
        TelegramBtns.btn_cancel,
        TelegramBtns.btn_save
    ),
    state=OrderState.adding_materials,
    parse_mode="HTML"
)


async def set_starting_state(callback: CallbackQuery, manager: DialogManager):
    state_object: FSMContext = manager.dialog_data.get("state_obj")
    cur_state = manager.dialog_data.get("cur_state")
    if state_object:
        await state_object.set_state(cur_state)


def create_orders_dialog():
    return Dialog(
        main_window,
        select_subject_window,
        price_window,
        input_deadline_window,
        input_description_window,
        materials_window,
        on_close=set_starting_state
    )
