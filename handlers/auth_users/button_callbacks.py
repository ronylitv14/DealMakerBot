from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.dialog import DialogManager

from handlers.auth_users.window_state import AuthStates

from database_api.components.users import Users
from database_api.components.balance import Balance

from keyboards.executor_auth_keyboard import create_inline_keyboard_executor_auth
from handlers.utils.email_utils import is_valid_email


class ButtonCallbacks:
    @staticmethod
    async def process_username(message: Message, input_widget: MessageInput, manager: DialogManager):
        username = message.text

        if username == message.from_user.username:
            await message.answer(
                text="<b>Варто придумати ім'я користувача в системі не ідентичне вашому ніку в Telegram!</b>",
                parse_mode="HTML"
            )
            return

        manager.dialog_data["username"] = username
        await manager.switch_to(AuthStates.get_email)

    @staticmethod
    async def process_email(message: Message, input_widget: MessageInput, manager: DialogManager):
        email = message.text or ""

        if is_valid_email(email):
            manager.dialog_data["email"] = email
            await manager.switch_to(state=AuthStates.get_password)
        else:
            await message.answer(
                text="<b>Даний email не є валідним!</b>",
                parse_mode="HTML"
            )

    @staticmethod
    async def process_password(message: Message, input_widget: MessageInput, manager: DialogManager):
        password = message.text
        if not password:
            await message.answer(
                text="Потрібно ввести пароль! Повторіть будь ласка)"
            )
        else:
            manager.dialog_data["first_password"] = password
            await manager.switch_to(state=AuthStates.repeat_password)

    @staticmethod
    async def save_user_data(message: Message, input_widget: MessageInput, manager: DialogManager):

        if manager.dialog_data["first_password"] == message.text:

            response = await Users().create_user(
                telegram_id=message.from_user.id,
                user_email=manager.dialog_data.get("email"),
                username=manager.dialog_data["username"],
                phone=manager.dialog_data["phone"],
                password=message.text,
                chat_id=message.chat.id,
                tg_username=manager.dialog_data.get("tg_username")
            ).do_request()

            if response.is_success:
                await manager.done()
                await Balance().post_user_balance(user_id=message.from_user.id).do_request()

                await message.answer(
                    text="Ваші дані успішно збережено!\n\n"
                         "Ви можете пройти реєстрацію на виконавця у нашій системі. Чи бажаєте ви зробити це зараз?",
                    reply_markup=create_inline_keyboard_executor_auth()
                )

            else:
                await message.answer(
                    text="Виникла помилка при збережені"
                )

        else:
            await message.answer(
                text="Паролі не співпадають! Повторіть будь ласка)"
            )

    @staticmethod
    async def cancel_auth(callback: CallbackQuery, button: Button, manager: DialogManager):
        await callback.message.answer(
            text="Гаразд! Ваша реєстрація відмінена"
        )
        await manager.done()
