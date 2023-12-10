from typing import Any

from aiogram_dialog.window import Window
from aiogram_dialog.dialog import Dialog
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.widgets.text import Const
from handlers.creating_executor_profile.window_state import CreatingProfile
from handlers.creating_executor_profile.window_widgets import TelegramBtns, TelegramInputs

from aiogram.fsm.context import FSMContext
from aiogram_dialog.dialog import DialogManager
from utils.dialog_categories import subject_titles


async def get_subjects(**kwargs):
    updated_subjects = []

    for ind, subject in enumerate(subject_titles):
        updated_subjects.append((subject, ind))

    return {
        "university_subjects": updated_subjects,
        "count": len(updated_subjects)
    }


description_window = Window(
    Const("<b>🖋 Розкажіть про себе!</b>\n"
          "<i>Нам цікаво дізнатися більше про вас. Можливо, ви хочете розповісти де ви навчалися, "
          "який у вас досвід роботи чи які ваши захоплення? Це допоможе нам краще вас пізнати!</i> 😊"),
    TelegramInputs.input_description,
    TelegramBtns.btn_cancel,
    state=CreatingProfile.adding_description,
    parse_mode="HTML"
)

subjects_window = Window(
    Const("Оберіть предмети, які ви можете виконувати"),
    TelegramInputs.input_subjects,
    TelegramBtns.btn_save_subjects,
    Row(
        TelegramBtns.btn_cancel,
        TelegramBtns.btn_back
    ),
    state=CreatingProfile.adding_subjects,
    parse_mode="HTML",
    getter=get_subjects
)

examples_window = Window(
    Const("<b>🎨 Приклади ваших робіт</b>\n"
          "<i>Якщо ви хочете поділитися своїми досягненнями або проектами, будь ласка, надайте приклади виконаних вами робіт."
          " Це може бути посилання на ваш портфоліо, фото проектів або "
          "будь-яка інша інформація, яка покаже нам ваші навички та досвід.</i> 🌟"),
    TelegramInputs.input_examples,
    Row(
        TelegramBtns.btn_cancel,
        TelegramBtns.btn_send_application,
    ),
    state=CreatingProfile.adding_task_examples,
    parse_mode="HTML"
)


async def on_dialog_close(data: Any, dialog_manager: DialogManager):
    cur_state = dialog_manager.dialog_data.get("cur_state")
    state: FSMContext = dialog_manager.dialog_data.get("state_obj")

    if state and cur_state:
        await state.set_state(cur_state)


def add_dialog_to_router(router) -> None:
    dialog = Dialog(
        description_window,
        subjects_window,
        examples_window,
        on_close=on_dialog_close
    )

    router.include_routers(dialog)
