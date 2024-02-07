from abc import ABC, abstractmethod
from typing import List, Any

from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.dialog import Dialog, DialogManager

from .window_state import *
from handlers.profile_instruments.window_widgets import TelegramBtns, TelegramInputs, ProfileBranch

state_to_update_obj_map = {
    EditPhone: ProfileBranch.PHONE,
    EditMail: ProfileBranch.EMAIL,
    EditNickName: ProfileBranch.NICKNAME,
    DeleteAccount: ProfileBranch.DELETE_ACCOUNT
}


class WindowBuilder(ABC):
    def __init__(self, state_group):
        self.state_group = state_group

    @abstractmethod
    def create_windows(self):
        pass


class EditMailWindowBuilder(WindowBuilder):
    def create_windows(self):
        auth_window = create_auth_window(self.state_group)
        edit_obj_window = create_edit_obj_window(
            self.state_group,
            Format("<b>📧Ваша попередня пошта:</b> {dialog_data[user][email]}\n"
                   "<i>Будь ласка, введіть нову електронну адресу.</i>"),
            ProfileBranch.EMAIL
        )
        accept_window = create_accept_window(
            self.state_group,
            Format("<b>✅ Підтвердження електронної адреси</b>\n"
                   "<i>Ви підтверджуєте вашу нову пошту:</i> {dialog_data[new_value]}?")
        )

        return auth_window, edit_obj_window, accept_window


class EditPhoneWindowBuilder(WindowBuilder):
    def create_windows(self):
        auth_window = create_auth_window(self.state_group)
        edit_obj_window = create_edit_obj_window(
            self.state_group,
            Format("<b>📧Ваш попередній номер телефону:</b> {dialog_data[user][phone]}\n"
                   "<i>Будь ласка, введіть новий номер.</i>"),
            ProfileBranch.PHONE
        )
        accept_window = create_accept_window(
            self.state_group,
            Format("<b>✅ Підтвердження номеру телефона</b>\n"
                   "<i>Ви підтверджуєте ваш новий номер:</i> {dialog_data[new_value]}?")
        )

        return auth_window, edit_obj_window, accept_window


class EditNickNameWindowBuilder(WindowBuilder):
    def create_windows(self):
        auth_window = create_auth_window(self.state_group)
        edit_obj_window = create_edit_obj_window(
            self.state_group,
            Format("<b>📧Ваш попередній nickname:</b> {dialog_data[user][username]}\n"
                   "<i>Будь ласка, введіть новий.</i>"),
            ProfileBranch.NICKNAME
        )
        accept_window = create_accept_window(
            self.state_group,
            Format("<b>✅ Підтвердження nickname</b>\n"
                   "<i>Ви підтверджуєте ваш новий nickname:</i> {dialog_data[new_value]}?")
        )

        return auth_window, edit_obj_window, accept_window


class DeleteAccWindowBuilder(WindowBuilder):
    def create_windows(self):
        auth_window = create_auth_window(self.state_group)
        accept_window = create_accept_window(
            self.state_group,
            Format("Ви справді хочете видалити аккаунт?")
        )

        return auth_window, accept_window


class WindowBuilderFactory:
    builder_classes = {}

    @classmethod
    def register_builder(cls, update_type: ProfileBranch, window_builder: type[WindowBuilder]):
        cls.builder_classes[update_type] = window_builder

    @classmethod
    def get_builder(cls, state_group, update_type: ProfileBranch) -> WindowBuilder:
        return cls.builder_classes[update_type](state_group)

    @classmethod
    def create_dialog(cls, state_group, update_type: ProfileBranch) -> Dialog:
        builder = cls.get_builder(state_group, update_type)
        if isinstance(builder, DeleteAccWindowBuilder):
            return Dialog(*builder.create_windows())
        return Dialog(*builder.create_windows())


WindowBuilderFactory.register_builder(ProfileBranch.EMAIL, EditMailWindowBuilder)
WindowBuilderFactory.register_builder(ProfileBranch.PHONE, EditPhoneWindowBuilder)
WindowBuilderFactory.register_builder(ProfileBranch.NICKNAME, EditNickNameWindowBuilder)
WindowBuilderFactory.register_builder(ProfileBranch.DELETE_ACCOUNT, DeleteAccWindowBuilder)


def create_auth_window(state_group):
    auth_user_window = Window(
        Const("<b>🔐 Введення паролю</b>\n"
              "<i>Будь ласка, введіть ваш пароль</i> для підтвердження операції."),
        TelegramInputs.input_password,
        TelegramBtns.cancel,
        state=state_group.auth_user,
        parse_mode="HTML"
    )
    return auth_user_window


def create_edit_obj_window(state_group, formatted_text: Format, updated_obj: ProfileBranch):
    return Window(
        formatted_text,
        TelegramInputs(updated_obj).construct_input_edited_obj(),
        TelegramBtns.cancel,
        state=state_group.edit_object,
        parse_mode="HTML"
    )


def create_accept_window(state_group, formatted_text: Format):
    return Window(
        formatted_text,
        TelegramBtns.accept_changes,
        TelegramBtns.cancel,
        state=state_group.accept_change,
        parse_mode="HTML"
    )


def create_dialogs():
    dialogs = []

    for state_group, update_obj in state_to_update_obj_map.items():
        dialogs.append(
            WindowBuilderFactory.create_dialog(
                state_group=state_group,
                update_type=update_obj
            )
        )

    return dialogs
