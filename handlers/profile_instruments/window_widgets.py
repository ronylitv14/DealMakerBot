import enum
from typing import Union, Callable, Awaitable
from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from handlers.profile_instruments.button_callbacks import ButtonCallbacks


class ProfileBranch(enum.Enum):
    EMAIL = 1
    PHONE = 2
    NICKNAME = 3
    DELETE_ACCOUNT = 4


class TelegramInputs:
    input_password = MessageInput(
        content_types=ContentType.TEXT,
        func=ButtonCallbacks.check_password
    )

    def __init__(self, updated_obj: ProfileBranch):
        self.updated_obj = updated_obj

    def construct_input_edited_obj(self):
        if self.updated_obj == ProfileBranch.EMAIL:
            func = ButtonCallbacks.update_obj_email
        elif self.updated_obj == ProfileBranch.PHONE:
            func = ButtonCallbacks.update_obj_phone
        else:
            func = ButtonCallbacks.update_obj_nickname

        input_edited_object = MessageInput(
            content_types=ContentType.TEXT,
            func=func
        )

        return input_edited_object


class TelegramBtns:
    accept_changes = Button(Const("Підтвердити"), id="b_accept", on_click=ButtonCallbacks.save_updated_obj)
    cancel = Button(Const("Відмінити"), id="b_cancel", on_click=ButtonCallbacks.cancel_dialog)
