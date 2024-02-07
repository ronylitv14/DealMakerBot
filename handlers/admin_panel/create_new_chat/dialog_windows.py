from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel, Back, Row
from aiogram_dialog.dialog import DialogManager, Dialog

from database_api.components.users import UserResponseList
from handlers.admin_panel.create_new_chat.dialog_widgets import TelegramInputs, TelegramBtns
from handlers.admin_panel.create_new_chat.dialog_states import CreatingCustomChat

from utils.dialog_categories import subject_titles


def get_data_about_user(user_type: str, dialog_manager: DialogManager):
    users = dialog_manager.dialog_data.get(user_type)

    res = []

    if users and isinstance(users, dict):
        users = UserResponseList(**users)
        for ind, user in enumerate(users):
            res.append((user, ind))

    return res


async def get_data_executors(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    return {
        "executors": get_data_about_user("executors", manager)
    }


async def get_data_clients(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    return {
        "clients": get_data_about_user("clients", manager)
    }


async def get_subject_data(**kwargs):
    res = []

    for ind, subject in enumerate(subject_titles):
        res.append((subject, ind))

    return {
        "subjects": res
    }


input_query_executor = Window(
    Format("Введіть ім'я користувача чи нікнейм в телеграмі для пошуку виконавців"),
    TelegramInputs.input_query_exec,
    Cancel(Format("Вийти")),
    state=CreatingCustomChat.query_executor
)

select_executor_window = Window(
    Format("Оберіть потрібного виконавця! Якщо його не було знайдено - поверніться до пошуку"),
    TelegramInputs.select_executor,
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти")),
    ),
    state=CreatingCustomChat.select_exec,
    getter=get_data_executors
)

input_query_client = Window(
    Format("Введіть ім'я користувача чи нікнейм в телеграмі для пошуку клієнта!"),
    TelegramInputs.input_query_client,
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти")),
    ),
    state=CreatingCustomChat.query_client
)

select_client_window = Window(
    Format("Оберіть потрібного клієнта! Якщо його не було знайдено - поверніться до пошуку"),
    TelegramInputs.select_client,
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти")),
    ),
    state=CreatingCustomChat.select_client,
    getter=get_data_clients
)

select_subject_window = Window(
    Format("Оберіть предмет щодо якого буду відбуватися замовлення"),
    TelegramInputs.select_subject,
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти")),
    ),
    state=CreatingCustomChat.add_subject,
    getter=get_subject_data
)

input_desc_window = Window(
    Format("Введіть зараз опис, який буде надіслано виконавцю та клієнту"),
    TelegramInputs.input_desc,
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти")),
    ),
    state=CreatingCustomChat.add_description
)

accept_deal = Window(
    Format("Це вікно підтвердження заданої вами інформації:\n\n"
           "Дані клієнта: {dialog_data[client_summary]}\n"
           "Дані виконавця: {dialog_data[executor_summary]}\n"
           "Предмет виконання: {dialog_data[subject]}\n"
           "Опис завдання, що буде надісланим обом:\n\n{dialog_data[description]}\n\n"
           "Якщо все описано вірно можна натискати кнопку 'Створити'"),
    Row(
        Back(Format("Назад")),
        Cancel(Format("Вийти")),
    ),
    TelegramBtns.btn_accept_deals,
    state=CreatingCustomChat.accept_all
)


def create_custom_chat_dialog():
    return Dialog(
        input_query_executor,
        select_executor_window,
        input_query_client,
        select_client_window,
        select_subject_window,
        input_desc_window,
        accept_deal
    )
