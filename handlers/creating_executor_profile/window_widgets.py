import operator

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Multiselect
from aiogram_dialog.widgets.kbd import ScrollingGroup, Back
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd.button import Button
from aiogram.enums.content_type import ContentType

from handlers.creating_orders import button_callbacks as files_callback
from handlers.creating_executor_profile.button_callbacks import ButtonCallbacks

subject_title_kdb = Multiselect(
    Format("✓ {item[0]}"),
    Format("{item[0]}"),
    id="m_subjects",
    item_id_getter=operator.itemgetter(1),
    items="university_subjects"
)


class TelegramInputs:
    input_description = MessageInput(
        func=ButtonCallbacks.process_description,
        content_types=ContentType.TEXT
    )

    input_subjects = ScrollingGroup(
        subject_title_kdb,
        id="sg_subject_title",
        width=2,
        height=7
    )

    input_examples = MessageInput(
        func=files_callback.ButtonCallbacks.preprocess_files_input,
        content_types=[ContentType.PHOTO, ContentType.DOCUMENT]
    )


class TelegramBtns:
    btn_cancel = Button(Const("Відмінити"), id="b_cancel", on_click=ButtonCallbacks.cancel_dialog)
    btn_save_subjects = Button(Const("Далі"), id="b_save", on_click=ButtonCallbacks.save_subjects)
    btn_send_application = Button(Const("Надіслати"), id="b_application",
                                  on_click=ButtonCallbacks.save_executor_application)
    btn_back = Back(Const("Назад"), id="b_back")
