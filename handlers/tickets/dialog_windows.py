from aiogram_dialog.window import Window
from aiogram_dialog.dialog import Dialog
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel, Back, Row

from handlers.tickets.window_state import Tickets
from handlers.tickets.window_widgets import TelegramBtns, TelegramInputs

from utils.dialog_categories import ticket_categories


async def get_ticket_subject_data(**kwargs):
    ticket_subjects = []

    for ind, subj in enumerate(ticket_categories):
        ticket_subjects.append((subj, ind))

    return {
        "subjects": ticket_subjects if ticket_subjects else [("Немає категорій", -1)]
    }


add_subject_window = Window(
    Format("Оберіть категорію тікету!"),
    TelegramInputs.ticket_subj_select,
    Cancel(Format("Вийти")),
    state=Tickets.add_subject,
    getter=get_ticket_subject_data
)

add_description_window = Window(
    Format("Тепер потрібно ввести текст для вашого тікету, який побачить адмін!"),
    TelegramInputs.input_description,
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти")),
    ),
    state=Tickets.add_description
)


def create_tickets_dialog():
    return Dialog(
        add_subject_window,
        add_description_window
    )
