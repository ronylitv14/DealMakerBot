from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row

from .window_state import AuthStates
from .window_widgets import (
    TelegramInputs,
    TelegramButtons
)

from utils.dialog_texts import (
    input_username_text,
    input_email_text,
    input_password_text,
    input_repeat_text
)

username_window = Window(
    Const(input_username_text),
    TelegramInputs.input_username,
    TelegramButtons.btn_cancel,
    state=AuthStates.get_username,
    parse_mode="HTML"
)

email_window = Window(
    Const(input_email_text),
    TelegramInputs.input_email,
    Row(
        TelegramButtons.btn_back,
        TelegramButtons.btn_skip
    ),
    state=AuthStates.get_email,
    parse_mode="HTML"
)

first_password_window = Window(
    Const(input_password_text),
    TelegramInputs.input_password,
    Row(
        TelegramButtons.btn_back,
        TelegramButtons.btn_cancel
    ),
    state=AuthStates.get_password,
    parse_mode="HTML"
)

second_password_window = Window(
    Const(input_repeat_text),
    TelegramInputs.input_confirm_password,
    Row(
        TelegramButtons.btn_back,
        TelegramButtons.btn_cancel
    ),
    state=AuthStates.repeat_password,
    parse_mode="HTML"
)
