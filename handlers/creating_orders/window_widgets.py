from aiogram.types.message import ContentType

import operator

from aiogram_dialog.widgets.kbd import Multiselect, ScrollingGroup
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog.widgets.kbd import Button, Back
from aiogram_dialog.widgets.kbd import Calendar, CalendarConfig
from aiogram_dialog.widgets.text import Const

from .button_callbacks import ButtonCallbacks
from .custom_widgets import CustomCalendar

task_type_kbd = Multiselect(
    Format("✓ {item[0]}"),
    Format("{item[0]}"),
    id="m_task_type",
    item_id_getter=operator.itemgetter(1),
    items="university_tasks"
)

subject_title_kdb = Multiselect(
    Format("✓ {item[0]}"),
    Format("{item[0]}"),
    id="m_subjects",
    item_id_getter=operator.itemgetter(1),
    items="university_subjects"
)


class TelegramInputs:
    order_type_select = ScrollingGroup(
        task_type_kbd,
        id="sg_task_type",
        width=2,
        height=5
    )

    subject_title_select = ScrollingGroup(
        subject_title_kdb,
        id="sg_subject_title",
        width=2,
        height=7
    )

    input_subject = MessageInput(
        content_types=ContentType.ANY,
        func=ButtonCallbacks.set_subject
    )

    input_price = MessageInput(
        content_types=ContentType.ANY,
        func=ButtonCallbacks.create_price,
    )

    input_deadline = CustomCalendar(
        id="id_calendar",
        on_click=ButtonCallbacks.set_deadline
    )

    input_docs = MessageInput(
        content_types=ContentType.ANY,
        func=ButtonCallbacks.preprocess_files_input
    )

    input_desc = MessageInput(
        content_types=ContentType.TEXT,
        func=ButtonCallbacks.preprocess_desc
    )


class TelegramBtns:
    btn_task_type = Button(Const("Далі"), id="go", on_click=ButtonCallbacks.saving_task_type_data)
    btn_subject = Button(Const("Далі"), id="subject_go", on_click=ButtonCallbacks.saving_subject_title_data)
    btn_set_unknown_price = Button(Const("Договірна"), id="set_price_unknown",
                                   on_click=ButtonCallbacks.set_price_unknown)
    btn_skip = Button(text=Const("Пропустити"), id="id_skip", on_click=ButtonCallbacks.skip_dialog_window)
    btn_back = Back(text=Const("Назад"))
    btn_cancel = Button(text=Const("Відмінити"), id="id_cancel", on_click=ButtonCallbacks.cancel_creating_order)
    btn_save = Button(text=Const("Зберегти"), id="id_save", on_click=ButtonCallbacks.save_order)
