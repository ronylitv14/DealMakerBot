from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.kbd import Row, Cancel
from database_api.components.chats import Chats, ChatModel
from database_api.components.tasks import Tasks, TaskModel

from aiogram_dialog.widgets.text import Format

from handlers.admin_panel.inactive_chat.dialog_states import InactiveChat
from handlers.admin_panel.inactive_chat.dialog_widgets import TelegramInput, TelegramBtns

query_window = Window(
    Format(
        "Потрібно ввести дані щодо чату, який потрібно деактивувати!\n\n"
        "Це може бути як просто у вигляді числа угоди: 1, 2, 3, 333 тощо. "
        "Так і у вигляді назви чату: Угода №1, Угода №123 тощо"
    ),
    TelegramInput.input_chat_id,
    Cancel(Format("Вийти")),
    state=InactiveChat.query_chat
)

acceptation_window = Window(
    Format(
        "Інформація щодо чату:\n\n{dialog_data[chat_summary]}\n\n{dialog_data[task_summary]}\n\n"
        "<b>Дані чату, який потрібно зробити вільним повністю відповідають цим даним?</b>"
    ),
    Row(
        TelegramBtns.btn_accept_deactivation,
        TelegramBtns.btn_reject_deactivation
    ),
    Cancel(Format("Вийти")),
    state=InactiveChat.accept_action,
    parse_mode="HTML"
)


def create_deactivation_chat_dialog():
    return Dialog(
        query_window,
        acceptation_window
    )
