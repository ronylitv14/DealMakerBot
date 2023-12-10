from aiogram_dialog.dialog import DialogManager, Dialog
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel, Back, Row

from handlers.deals_executor.dialog_states import DealsExecutor
from handlers.deals_executor.dialog_widgets import TelegramBtns, TelegramInputs


async def get_user_data(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    users = manager.dialog_data.get("users")

    res = []

    for ind, user in enumerate(users):
        res.append((user, ind))

    return {
        "users": res if res else [("Немає відповідних даних", -1)]
    }


input_query_window = Window(
    Format("Напишіть зараз приблизне ім'я користувача для створення угоди!"),
    TelegramInputs.input_username,
    Cancel(Format("Вийти")),
    state=DealsExecutor.query_user
)

choose_user = Window(
    Format("Тепер оберіть користувача з можливих варіантів!"),
    TelegramInputs.select_user,
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти"))
    ),
    state=DealsExecutor.choose_user,
    getter=get_user_data
)


def create_dialog_deal_executor():
    return Dialog(
        input_query_window,
        choose_user
    )
