from aiogram.types import Message, CallbackQuery

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.dialog import DialogManager

from .window_state import AuthStates
from database.crud import save_user_to_db, create_user_balance
from keyboards.clients import create_keyboard_client
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

        # await save_user_to_db(
        #     telegram_id=message.from_user.id,
        #     username=manager.dialog_data["username"],
        #     phone=manager.dialog_data["phone"],
        #     email=email
        # )
        # await manager.done()
        # await message.answer(
        #     text="Ваші дані успішно збережені",
        #     reply_markup=create_keyboard_client()
        # )

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
            saved_user = await save_user_to_db(
                telegram_id=message.from_user.id,
                username=manager.dialog_data["username"],
                phone=manager.dialog_data["phone"],
                password=message.text,
                chat_id=message.chat.id,
                tg_username=manager.dialog_data.get("tg_username")
            )

            if saved_user:
                await manager.done()
                await create_user_balance(user_id=message.from_user.id)
                await message.answer(
                    text="Ваші дані успішно збережені",
                    reply_markup=create_keyboard_client()
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

    @staticmethod
    async def save_auth(callback: CallbackQuery, button: Button, manager: DialogManager):
        await manager.done()
        await callback.message.answer(
            text="Ваші дані успішно збережено!",
            reply_markup=create_keyboard_client()
        )
