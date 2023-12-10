from handlers.admin_panel.window_states import BanUser

from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Cancel, Back
from aiogram_dialog.dialog import Dialog
from aiogram_dialog.window import Window

from handlers.admin_panel.regulations.message_input import input_warning
from handlers.admin_panel.regulations.button_callbacks import ban_user, unban_user, add_warning

btn_ban_user = Button(Const("Забанити користувача"), id="btn_ban", on_click=ban_user)
btn_unban_user = Button(Const("Розбанити користувача"), id="btn_unban", on_click=unban_user)
btn_add_warning = Button(Const("Видати попередження"), id="btn_warning", on_click=add_warning)

bans_window = Window(
    Format("Ім'я користувача: {start_data[user].username}\n"
           "Нік в телеграмі: {start_data[user].telegram_username}"),
    btn_ban_user,
    btn_unban_user,
    btn_add_warning,
    Cancel(Const("Назад")),
    state=BanUser.main_window
)

warning_window = Window(
    Format("Тут введіть для нього попередження"),
    input_warning,
    Back(Const("Назад")),
    Cancel(Const("Вийти")),
    state=BanUser.add_warning
)


def create_regulations_dialog():
    return Dialog(
        bans_window,
        warning_window
    )
