import re
from abc import ABC, abstractmethod

from aiogram.types import Message, CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from handlers.states_handler import ClientDialog, ExecutorDialog
from keyboards.clients import create_profile_instruments
from database.crud import get_user_auth, update_user_email, update_user_nickname, update_user_phone, delete_user_from_db
from database.models import User
from handlers.utils.command_utils import show_menu

PHONE_REGEX = r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"


def wrapper(func):
    async def decorator(callback: CallbackQuery, button: Button, manager: DialogManager):
        await func(callback, button, manager)
        cur_state = manager.dialog_data.get("cur_state")
        if manager.dialog_data.get("delete"):
            return await show_menu(callback.message, manager.dialog_data.get("state"))

        if cur_state == ClientDialog.profile:
            await callback.message.answer(
                text="Ви вийшли з даного діалогу",
                reply_markup=create_profile_instruments()
            )
        elif cur_state == ExecutorDialog.profile:
            await callback.message.answer(
                text="Ви вийшли з даного діалогу",
                reply_markup=create_profile_instruments()
            )
        await manager.done()

    return decorator


class UpdateStrategy(ABC):
    @abstractmethod
    async def validate_and_update(self, message: Message, widget: MessageInput, manager: DialogManager):
        pass


class EmailUpdateStrategy(UpdateStrategy):
    async def validate_and_update(self, message: Message, widget: MessageInput, manager: DialogManager):
        items = message.entities or []
        email = None

        if not items:
            await message.answer(text="Пошта введена не коректно")
            return

        for item in items:
            if item.type == "email":
                email = item.extract_from(message.text)

        manager.dialog_data["update_function"] = update_user_email
        return email


class NicknameUpdateStrategy(UpdateStrategy):
    async def validate_and_update(self, message: Message, widget: MessageInput, manager: DialogManager):
        nickname = message.text

        if nickname == message.from_user.username:
            await message.answer(
                text="Не використовуй свій нікнейм в телеграмі"
            )
            return

        manager.dialog_data["update_function"] = update_user_nickname
        return nickname


class PhoneUpdateStrategy(UpdateStrategy):
    async def validate_and_update(self, message: Message, widget: MessageInput, manager: DialogManager):
        phone = message.text

        matched_pattern = re.match(PHONE_REGEX, phone)
        if not matched_pattern:
            await message.answer(
                text="Invalid phone"
            )
            return

        phone = matched_pattern.group()
        manager.dialog_data["update_function"] = update_user_phone
        return phone


class UpdateContext:
    def __init__(self, strategy: UpdateStrategy):
        self._strategy = strategy

    async def execute_update(self, message: Message, widget: MessageInput, manager: DialogManager):
        updated_value = await self._strategy.validate_and_update(message, widget, manager)
        if updated_value:
            manager.dialog_data["updated_obj"] = updated_value
            await manager.next()


class ButtonCallbacks:
    @staticmethod
    async def check_password(message: Message, widget: MessageInput, manager: DialogManager):
        user_id = message.from_user.id
        password = message.text
        user: User = await get_user_auth(user_id)

        if not user:
            return await message.answer(
                text="You are not in db"
            )

        is_correct = user.check_password(password=password)
        if is_correct:
            manager.dialog_data["user"] = user
            await manager.next()
        else:
            await message.answer(
                text="Incorrect password"
            )

    @staticmethod
    async def update_obj_email(message: Message, widget: MessageInput, manager: DialogManager, *args):
        update_context = UpdateContext(EmailUpdateStrategy())
        await update_context.execute_update(
            message, widget, manager
        )

    @staticmethod
    async def update_obj_nickname(message: Message, widget: MessageInput, manager: DialogManager, *args):
        update_context = UpdateContext(NicknameUpdateStrategy())
        await update_context.execute_update(
            message, widget, manager
        )

    @staticmethod
    async def update_obj_phone(message: Message, widget: MessageInput, manager: DialogManager, *args):
        update_context = UpdateContext(PhoneUpdateStrategy())
        await update_context.execute_update(
            message, widget, manager
        )

    @staticmethod
    @wrapper
    async def save_updated_obj(callback: CallbackQuery, button: Button, manager: DialogManager):
        update_function = manager.dialog_data.get("update_function")
        update_obj = manager.dialog_data.get("updated_obj")
        delete = manager.dialog_data.get("delete")
        if update_function and update_obj:
            await update_function(
                callback.from_user.id,
                update_obj
            )
        elif delete:

            await delete_user_from_db(
                user_id=callback.from_user.id
            )
    @staticmethod
    @wrapper
    async def cancel_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        pass
