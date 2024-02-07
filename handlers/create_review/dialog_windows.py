from typing import Any

from aiogram_dialog import Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, Row
from aiogram_dialog.window import Window

from aiogram_dialog.widgets.text import Const, Format
from keyboards.main import create_keyboard_by_state

from handlers.create_review.dialog_states import ReviewStates
from handlers.create_review.dialog_widgets import TelegramWidgets, TelegramBtns, ScrollingSights, create_cancel_button, \
    create_back_button, create_skip_button

from utils.dialog_categories import positive_aspects, negative_aspects, rating_stars
from utils.dialog_texts import select_user_rating_text, comment_text


def get_data(collection_name: str, items: list):
    res = []

    for ind, val in enumerate(items):
        if collection_name == "ratings":
            ind += 1
        res.append((val, ind))

    return {
        collection_name: res
    }


async def get_positives_data(**kwargs):
    return get_data("positives", positive_aspects)


async def get_negatives_data(**kwargs):
    return get_data("negatives", negative_aspects)


async def get_ratings_data(**kwargs):
    return get_data("ratings", rating_stars)


rating_window = Window(
    Format(select_user_rating_text),
    TelegramWidgets.input_rating,
    create_cancel_button("Вийти"),
    state=ReviewStates.specify_rating,
    getter=get_ratings_data,
    parse_mode="HTML",
)

positives_window = Window(
    Format("Оберіть позитивні риси користувача за наявності!"),
    ScrollingSights.input_positives,
    Row(
        create_back_button("Назад"),
        create_cancel_button("Вийти"),
        create_skip_button("Далі")
    ),
    state=ReviewStates.choose_positives,
    getter=get_positives_data
)

negatives_window = Window(
    Format("Оберіть негативні риси користувача за наявності!"),
    ScrollingSights.input_negatives,
    Row(
        create_back_button("Назад"),
        create_cancel_button("Вийти"),
        create_skip_button("Далі")
    ),
    state=ReviewStates.choose_negatives,
    getter=get_negatives_data,
)

commentary_window = Window(
    Format(comment_text),
    Row(
        create_back_button("Назад"),
        create_cancel_button("Вийти"),
    ),
    TelegramBtns.btn_save_dialog,
    state=ReviewStates.add_comment,
    parse_mode="HTML"
)


async def on_dialog_close(data: Any, dialog_manager: DialogManager, **kwargs):
    cur_state = dialog_manager.start_data.get("cur_state")
    await create_keyboard_by_state(cur_state, dialog_manager)


def create_review_dialog():
    return Dialog(
        rating_window,
        positives_window,
        negatives_window,
        commentary_window,
        on_close=on_dialog_close,
    )
